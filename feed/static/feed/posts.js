function getPostsHtml(postFetchers) {
    var posts = []
    for (var i = 0; i < postFetchers.length; ++i) {
        var li = document.createElement("li");
        var content = document.createTextNode("At post fetcher " + (i + 1));
        li.appendChild(content);
        posts.push(li);
    }
    return posts;
}
