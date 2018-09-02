var POSTS_PER_PAGE = 25;

function setupPagination(nextBtn, prevBtn, setPosts) {
    var posts = [];
    var currentPage = -1;
    var morePosts = true;
    prevBtn.disabled = true;

    function getMorePosts() {
        newPosts = getPostsHtml(POSTS_PER_PAGE);
        if (!newPosts || newPosts.length === 0) {
            morePosts = false;
        }
        posts = posts.concat(newPosts);
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

    function nextPage() {
        currentPage += 1;
        if (currentPage > 0) {
            prevBtn.disabled = false;
        }

        while ((currentPage + 1) * POSTS_PER_PAGE >= posts.length) {
            if (morePosts) {
                getMorePosts();
            } else {
                nextBtn.disabled = true;
                break;
            }
        }

        setPosts(posts.slice(currentPage, currentPage + POSTS_PER_PAGE));
    }

    nextPage();

    prevBtn.onclick = prevPage;
    nextBtn.onclick = nextPage;
}
