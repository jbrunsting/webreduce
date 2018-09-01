var postFetchers = []
var previousResults = []
var unusedPosts = []
var noMorePosts = []

function setPostFetchers(fetchers) {
    postFetchers = fetchers;
    for (var i = 0; i < postFetchers.length; ++i) {
        unusedPosts[i] = [];
        noMorePosts[i] = false; fetchMorePosts(i);
    }
}

function fetchMorePosts(fetcherIndex) {
    if (noMorePosts[fetcherIndex]) {
        return;
    }

    var result;
    if (previousResults[fetcherIndex] && previousResults[fetcherIndex].paginationData) {
        result = postFetchers[fetcherIndex](previousResults[fetcherIndex].paginationData);
    } else if (previousResults[fetcherIndex]) {
        // If there is no pagination data, and we already made a call, don't
        // try and get the next page since the request must not be paginated
        noMorePosts[fetcherIndex] = true;
        return;
    } else {
        result = postFetchers[fetcherIndex]();
    }

    if (!result || !Array.isArray(result.posts) || result.posts.length == 0) {
        noMorePosts[fetcherIndex] = true;
        return;
    }

    previousResults[fetcherIndex] = result;

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
        noMorePosts[fetcherIndex] = true
        return;
    }

    filteredPosts.sort(function(a, b) {
        return b.date - a.date;
    });

    unusedPosts[fetcherIndex] = unusedPosts[fetcherIndex].concat(filteredPosts);
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

function getNextPost() {
    var postIndex;
    for (var i = 0; i < postFetchers.length; ++i) {
        if (unusedPosts[i].length == 0) {
            fetchMorePosts(i);
        }

        if (noMorePosts[i]) {
            continue;
        }

        if (!postIndex || unusedPosts[i][0].date < unusedPosts[postIndex][0].date) {
            postIndex = i;
        }
    }

    if (!postIndex) {
        return;
    }

    return unusedPosts[postIndex].pop();
}

function getPostsHtml(count) {
    var postsContent = [];
    for (var i = 0; i < count; ++i) {
        var nextPost = getNextPost();
        if (!nextPost) {
            return postsContent;
        }
        postsContent.push(getPostHtml(nextPost));
    }

    return postsContent;
}
