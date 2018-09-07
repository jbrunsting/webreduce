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
    var postContent = document.createElement("li");

    var header = document.createElement("header");

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
    header.appendChild(date);

    postContent.appendChild(header);

    if (post.author) {
        var author = document.createElement("p");
        author.appendChild(document.createTextNode(post.author));
        postContent.appendChild(author);
    }

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
        getHandlerPosts(handler, function() {
            if (timedOut) {
                return;
            }

            --handlersPending;
            handlersComplete[i] = true;
            if (handlersPending <= 0) {
                callback();
            }
        });
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

    return generator;
}
