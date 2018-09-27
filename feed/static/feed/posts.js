var POST_BUFFER_SIZE = 10;
var HANDLER_TIMEOUT = 10000;

function getHandlerPosts(handler, callback) {
    if (handler.noMorePosts) {
        callback();
        return;
    }

    function onResult(result) {
        if (!result || !Array.isArray(result.posts) || result.posts.length == 0) {
            handler.noMorePosts = true;
            callback();
            return;
        }

        handler.previousResult = result;

        var filteredPosts = []
        for (var i = 0; i < result.posts.length; ++i) {
            post = result.posts[i];
            if (!post.title) {
                console.error("Post has no title: " + JSON.stringify(post));
                continue;
            }

            if (!post.date instanceof Date || isNaN(post.date)) {
                console.error("Post has an invalid date: " + JSON.stringify(post));
                continue;
            }

            filteredPosts.push(post);
        }

        if (filteredPosts.length == 0) {
            handler.noMorePosts = true
            callback();
            return;
        }

        handler.unusedPosts = handler.unusedPosts.concat(filteredPosts);
        callback();
    }

    var result;
    if (handler.previousResult && handler.previousResult.paginationData) {
        handler.fetchPosts(onResult, handler.previousResult.paginationData);
    } else if (handler.previousResult) {
        // If there is no pagination data, and we already made a call, don't
        // try and get the next page since the request must not be paginated
        handler.noMorePosts = true;
        callback();
        return;
    } else {
        handler.fetchPosts(onResult);
    }
}

function getPostHtml(post) {
    var postContent = $("<li>");
    postContent.addClass("card");

    var header = $("<header>");
    header.addClass("post-header");

    var title = $("<h3>");
    title.append(post.title);

    if (post.link) {
        var titleLink = $("<a>");
        titleLink.attr("href", post.link);
        titleLink.append(title);
        header.append(titleLink);
    } else {
        header.append(title);
    }

    var date = $("<p>");
    date.append((new Date(post.date)).toLocaleString());
    date.addClass("subtitle");
    header.append(date);

    if (post.author) {
        var author = $("<p>");
        author.append(post.author);
        author.addClass("subtitle");
        header.append(author);
    }

    if (post.comments) {
        var commentsLink = $("<a>");
        commentsLink.attr("href", post.comments);
        commentsLink.append("comments");
        var comments = $("<p>");
        comments.append(commentsLink);
        comments.addClass("subtitle");
        header.append(comments);
    }

    if (post.icon) {
        var icon = $("<img>");
        icon.src = post.icon;
        icon.addClass("favicon");
        header.append(icon);
    }

    postContent.append(header);

    if (post.content) {
        var checkbox = $("<input>");
        checkbox.addClass("collapser");
        checkbox.attr("type", "checkbox");
        checkbox.attr("id", "checkbox-" + Math.round(Math.random() * 100000000));

        var label = $("<label>");
        label.attr("for", checkbox.attr("id"));
        label.addClass("collapse-button");
        label.addClass("collapse-icon bottom");

        var content = $("<div>");
        var contentDoc = new DOMParser().parseFromString(post.content, "text/html");
        content.html(contentDoc.documentElement.textContent);
        content.addClass("expandable");
        postContent.append(content);
        postContent.prepend(checkbox);
        postContent.append(label);
    }

    return postContent;
}

function fillPostBuffers(subscriptionHandlers, callback) {
    var timedOut = false;
    var handlersNeedingPosts = [];
    var handlersComplete = [];
    subscriptionHandlers.forEach(function(handler) {
        if (!handler.noMorePosts && handler.unusedPosts.length < POST_BUFFER_SIZE) {
            handlersNeedingPosts.push(handler);
        }
    });

    if (handlersNeedingPosts.length == 0) {
        callback();
        return;
    }

    var handlersPending = handlersNeedingPosts.length;

    handlersNeedingPosts.forEach(function(handler, i) {
        function onHandlerComplete() {
            if (timedOut) {
                return;
            }
            --handlersPending;
            handlersComplete[i] = true;
            if (handlersPending <= 0) {
                callback();
            }
        }

        try {
            getHandlerPosts(handler, onHandlerComplete);
        } catch (e) {
            console.error("Plugin " + handler.pluginName + " threw an error while fetching posts: " + e);
            handler.noMorePosts = true;
            onHandlerComplete();
        }
    });

    setTimeout(function() {
        if (handlersPending <= 0) {
            return;
        }

        timedOut = true;
        handlersNeedingPosts.forEach(function(handler, i) {
            if (!handlersComplete[i]) {
                handler.noMorePosts = true;
                console.error("Plugin " + handler.pluginName + " timed out");
            }
        });

        callback();
    }, HANDLER_TIMEOUT);
}

var HANDLER_LOOKBACK = 10;
var lastUsedHandlers = []

var SCORE_FOR_PRECEEDING = 2;
var MAX_DATE_SCORE = 3;
var DATE_SCORE_SCALING_FACTOR = 10000000; // 3 hours for ~1 point
function getBestHandler(handlerOne, handlerTwo) {
    var dateDiff = handlerOne.unusedPosts[0].date - handlerTwo.unusedPosts[0].date;
    var dateScoreDiff = Math.max(Math.min(dateDiff / 10000, MAX_DATE_SCORE), -MAX_DATE_SCORE);

    var handlerOneOccurences = $.grep(lastUsedHandlers, function(handler) {
        return handler.pluginName === handlerOne.pluginName;
    }).length;

    var handlerTwoOccurences = $.grep(lastUsedHandlers, function(handler) {
        return handler.pluginName === handlerTwo.pluginName;
    }).length;

    var handlerOneScore = (HANDLER_LOOKBACK - handlerOneOccurences) + dateScoreDiff;
    var handlerTwoScore = (HANDLER_LOOKBACK - handlerTwoOccurences) - dateScoreDiff;

    if (lastUsedHandlers.length != 0) {
        lastUsed = lastUsedHandlers[lastUsedHandlers.length - 1];
        if (lastUsed.pluginName === handlerOne.pluginName) {
            handlerOneScore += SCORE_FOR_PRECEEDING;
        } else if (lastUsed == handlerTwo) {
            handlerTwoScore += SCORE_FOR_PRECEEDING;
        }
    }

    if (handlerOneScore > handlerTwoScore) {
        return handlerOne;
    }

    return handlerTwo;
}

function getNextPost(subscriptionHandlers, callback) {
    fillPostBuffers(subscriptionHandlers, function() {
        var handlerToUse;
        subscriptionHandlers.forEach(function(handler) {
            if (handler.unusedPosts.length == 0) {
                return;
            }

            if (!handlerToUse) {
                handlerToUse = handler;
            }

            handlerToUse = getBestHandler(handlerToUse, handler);
        });

        if (!handlerToUse) {
            callback();
            return;
        }

        lastUsedHandlers.push(handlerToUse);
        lastUsedHandlers = lastUsedHandlers.slice(lastUsedHandlers.length - HANDLER_LOOKBACK, lastUsedHandlers.length);

        callback(handlerToUse.unusedPosts.shift());
    });
}

function getPostsHtml(subscriptionHandlers, count, callback) {
    var postsContent = [];
    var onGotPost = function(post) {
        if (post) {
            var postHtml = getPostHtml(post);
            postsContent.push(postHtml);
            if (postsContent.length >= count) {
                callback(postsContent);
            } else {
                getNextPost(subscriptionHandlers, onGotPost);
            }
        } else {
            callback(postsContent);
        }
    }
    getNextPost(subscriptionHandlers, onGotPost);
}

function PostGenerator() {
    var generator = {};

    var subscriptionHandlers = [];
    generator.setSubscriptions = function(subscriptions) {
        subscriptions.forEach(function(subscription) {
            if (!subscription.fetchPosts) {
                return;
            }

            handler = {};
            handler.fetchPosts = function(callback, paginationData) {
                return subscription.fetchPosts(callback, subscription.config, paginationData);
            }
            handler.pluginName = subscription.pluginName;
            handler.unusedPosts = [];
            handler.noMorePosts = false;
            subscriptionHandlers.push(handler);
        });
    }

    generator.getPostsHtml = function(count, callback) {
        return getPostsHtml(subscriptionHandlers, count, callback);
    }

    generator.hasMorePosts = function() {
        return subscriptionHandlers.some(function(handler) {
            return !handler.noMorePosts;
        });
    }

    return generator;
}


var removeExistingScrollListener;

function setupPostList(postGenerator, postList, loadingPlaceholder, emptyPlaceholder) {
    var POSTS_PER_PAGE = 5;
    var POST_BUFFER = 200;
    var NUM_PLACEHOLDERS = 2;

    if (removeExistingScrollListener) {
        removeExistingScrollListener();
    }

    var loadingPosts = false;
    var postsToRemove = postList.children().length - NUM_PLACEHOLDERS;
    postList.children().filter(":lt(" + postsToRemove + ")").remove();

    if (!postGenerator.hasMorePosts()) {
        loadingPlaceholder.hide();
        emptyPlaceholder.show();
        return;
    }

    function getMorePosts(onComplete) {
        if (loadingPosts) {
            return;
        }

        loadingPosts = true;
        postGenerator.getPostsHtml(POSTS_PER_PAGE, function(posts) {
            posts.forEach(function(post) {
                loadingPlaceholder.before(post);
            });

            if (!postGenerator.hasMorePosts()) {
                loadingPlaceholder.hide();
                if (postList.children().length == NUM_PLACEHOLDERS) {
                    emptyPlaceholder.show();
                }
            }

            loadingPosts = false;
            onComplete();
        });
    }

    var documentNode = $(document);
    var windowNode = $(window);

    function getPostsIfRequired() {
        if (!loadingPosts && postGenerator.hasMorePosts() && documentNode.height() - documentNode.scrollTop() <= windowNode.height() + POST_BUFFER) {
            getMorePosts(getPostsIfRequired);
        }
    }

    getPostsIfRequired();

    var scrollHandler = function() {
        getPostsIfRequired();
    }

    windowNode.on("scroll", scrollHandler);

    removeExistingScrollListener = function() {
        windowNode.off("scroll", scrollHandler);
    }
}
