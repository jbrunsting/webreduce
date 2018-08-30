previousResults = []

function getPosts(postFetchers) {
    var posts = [];
    for (var i = 0; i < postFetchers.length; ++i) {
        var result;
        if (previousResults.length == 0) {
            result = postFetchers[i](previousResults[i]);
        } else {
            result = postFetchers[i]();
        }

        previousResults[i] = result;
        if (result && Array.isArray(result.posts)) {
            posts = posts.concat(result.posts);
        }
    }

    return posts;
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

function getPostsHtml(postFetchers) {
    var posts = getPosts(postFetchers);
    var filteredPosts = []

    console.log("Posts are " + JSON.stringify(posts));
    for (var i = 0; i < posts.length; ++i) {
        post = posts[i];
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

    filteredPosts.sort(function(a, b) {
        return b.date - a.date;
    });

    var postsContent = [];
    for (var i = 0; i < filteredPosts.length; ++i) {
        postsContent.push(getPostHtml(filteredPosts[i]));
    }

    return postsContent;
}
