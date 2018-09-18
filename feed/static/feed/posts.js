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

// TODO: Jquery!
function getPostHtml(post) {
    var postContent = document.createElement("li");

    var header = document.createElement("header");
    header.classList.add("post-header");

    var title = document.createElement("h3");
    title.appendChild(document.createTextNode(post.title));

    if (post.link) {
        var titleLink = document.createElement("a");
        titleLink.href = post.link
        titleLink.appendChild(title);
        header.appendChild(titleLink);
    } else {
        header.appendChild(title);
    }

    var date = document.createElement("p");
    date.appendChild(document.createTextNode((new Date(post.date)).toLocaleString()));
    date.classList.add("subtitle");
    header.appendChild(date);

    if (post.author) {
        var author = document.createElement("p");
        author.appendChild(document.createTextNode(post.author));
        author.classList.add("subtitle");
        header.appendChild(author);
    }

    if (post.icon) {
        var icon = document.createElement("img");
        icon.src = post.icon;
        icon.classList.add("favicon");
        header.appendChild(icon);
    }

    postContent.appendChild(header);

    if (post.content) {
        var content = document.createElement("div");
        content.innerHTML = post.content;
        postContent.appendChild(content);
    }

    if (post.comments) {
        var commentsLink = document.createElement("a");
        commentsLink.href = post.comments;
        var comments = document.createElement("p");
        comments.appendChild(document.createTextNode("comments"));
        commentsLink.appendChild(comments);
        commentsLink.classList.add("subtitle");
        postContent.appendChild(commentsLink);
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

function getNextPost(subscriptionHandlers, callback) {
    fillPostBuffers(subscriptionHandlers, function() {
        var handlerToUse;
        subscriptionHandlers.forEach(function(handler) {
            if (handler.unusedPosts.length == 0) {
                return;
            }

            if (!handlerToUse || handler.unusedPosts[0].date < handlerToUse.unusedPosts[0].date) {
                handlerToUse = handler;
            }
        });

        if (!handlerToUse) {
            callback();
            return;
        }

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
