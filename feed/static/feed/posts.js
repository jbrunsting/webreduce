function getHandlerPosts(handler) {
    if (handler.noMorePosts) {
        return;
    }

    var result;
    if (handler.previousResult && handler.previousResult.paginationData) {
        result = handler.fetchPosts(handler.previousResult.paginationData);
    } else if (handler.previousResult) {
        // If there is no pagination data, and we already made a call, don't
        // try and get the next page since the request must not be paginated
        handler.noMorePosts = true;
        return;
    } else {
        result = handler.fetchPosts();
    }

    if (!result || !Array.isArray(result.posts) || result.posts.length == 0) {
        handler.noMorePosts = true;
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
        return;
    }

    filteredPosts.sort(function(a, b) {
        return b.date - a.date;
    });

    handler.unusedPosts = handler.unusedPosts.concat(filteredPosts);
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
    date.appendChild(document.createTextNode(post.date.toLocaleString()));
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

function getNextPost(subscriptionHandlers) {
    var handlerToUse;
    subscriptionHandlers.forEach(function(handler) {
        if (handler.noMorePosts) {
            return;
        }

        if (handler.unusedPosts.length == 0) {
            getHandlerPosts(handler);
        }

        if (handler.noMorePosts) {
            return;
        }

        if (!handlerToUse || handler.unusedPosts[0].date < handlerToUse.unusedPosts[0].date) {
            handlerToUse = handler;
        }
    });

    if (!handlerToUse) {
        return;
    }

    return handlerToUse.unusedPosts.pop();
}

function getPostsHtml(subscriptionHandlers, count) {
    var postsContent = [];
    for (var i = 0; i < count; ++i) {
        var nextPost = getNextPost(subscriptionHandlers);
        if (!nextPost) {
            return postsContent;
        }
        postsContent.push(getPostHtml(nextPost));
    }

    return postsContent;
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
            handler.fetchPosts = subscription.fetchPosts;
            handler.unusedPosts = [];
            handler.noMorePosts = false;
            subscriptionHandlers.push(handler);
        });
    }

    generator.getPostsHtml = function(count) {
        return getPostsHtml(subscriptionHandlers, count);
    }

    return generator;
}
