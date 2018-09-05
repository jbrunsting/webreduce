var POST_BUFFER_SIZE = 10;
var HANDLER_TIMEOUT = 15000;

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
                console.log("Post has no title: " + JSON.stringify(post));
                continue;
            }

            if (!post.date instanceof Date || isNaN(post.date)) {
                console.log("Post has an invalid date" + JSON.stringify(post));
                continue;
            }

            filteredPosts.push(post);
        }

        if (filteredPosts.length == 0) {
            handler.noMorePosts = true
            callback();
            return;
        }

        filteredPosts.sort(function(a, b) {
            return b.date - a.date;
        });

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

    var title = document.createElement("h2");
    title.appendChild(document.createTextNode(post.title));

    if (post.link) {
        var titleLink = document.createElement("a");
        titleLink.href = post.link
        titleLink.appendChild(title);
        postContent.appendChild(titleLink);
    } else {
        postContent.appendChild(title);
    }

    var date = document.createElement("p");
    date.appendChild(document.createTextNode((new Date(post.date)).toLocaleString()));
    postContent.appendChild(date);

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
    subscriptionHandlers.forEach(function(handler) {
        if (!handler.noMorePosts && handler.unusedPosts.length < POST_BUFFER_SIZE) {
            handlersNeedingPosts.push(handler);
        }
    });

    if (handlersNeedingPosts.length == 0) {
        callback();
        return;
    }

    handlersNeedingPosts.forEach(function(handler) {
        getHandlerPosts(handler, function() {
            if (timedOut) {
                return;
            }

            handlersNeedingPosts.splice(handlersNeedingPosts.indexOf(handler), 1);
            if (handlersNeedingPosts.length == 0) {
                callback();
            }
        });
    });

    setTimeout(function() {
        if (handlersNeedingPosts.length == 0) {
            return;
        }

        timedOut = true;
        handlersNeedingPosts.forEach(function(handler) {
            console.error("Plugin " + handler.pluginName + " timed out while getting posts");
            handler.timedOut = true;
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

        callback(handlerToUse.unusedPosts.pop());
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
            handler.timedOut = false;
            subscriptionHandlers.push(handler);
        });
    }

    generator.getPostsHtml = function(count, callback) {
        return getPostsHtml(subscriptionHandlers, count, callback);
    }

    return generator;
}
