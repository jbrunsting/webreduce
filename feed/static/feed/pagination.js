var POSTS_PER_PAGE = 25;

function setupPagination(postGenerator, nextBtn, prevBtn, setPosts) {
    var posts = [];
    var currentPage = -1;
    var morePosts = true;
    nextBtn.disabled = true;
    prevBtn.disabled = true;

    function getMorePosts(callback) {
        postGenerator.getPostsHtml(POSTS_PER_PAGE, function(newPosts) {
            if (!newPosts || newPosts.length === 0) {
                morePosts = false;
            }
            posts = posts.concat(newPosts);
            callback();
        });
    }

    function prevPage() {
        nextBtn.disabled = false;

        currentPage -= 1;
        if (currentPage == 0) {
            prevBtn.disabled = true;
        }

        firstPost = currentPage * POSTS_PER_PAGE;
        setPosts(posts.slice(currentPage, currentPage + POSTS_PER_PAGE));
    }

    function bufferNextPage(callback) {
        if ((currentPage + 2) * POSTS_PER_PAGE >= posts.length) {
            if (morePosts) {
                getMorePosts(function() {
                    bufferNextPage(callback);
                });
            } else {
                callback((currentPage + 1) * POSTS_PER_PAGE < posts.length);
            }
        } else {
            callback(true);
        }
    }

    function nextPage() {
        currentPage += 1;
        if (currentPage > 0) {
            prevBtn.disabled = false;
        }

        setPosts(posts.slice(currentPage, currentPage + POSTS_PER_PAGE));

        nextBtn.disabled = true;
        bufferNextPage(function(hasNextPage) {
            nextBtn.disabled = !hasNextPage;
        });
    }

    bufferNextPage(function(hasNextPage) {
        if (hasNextPage) {
            nextPage();
        }
    });

    prevBtn.onclick = prevPage;
    nextBtn.onclick = nextPage;
}
