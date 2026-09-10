document.addEventListener("DOMContentLoaded", function () {

    console.log("NewsPulseHQ loaded successfully.");

    /*
    =========================
    LIKE BUTTON
    =========================
    */

    const likeButton = document.getElementById("like-button");

    if (likeButton) {

        likeButton.addEventListener("click", function (event) {

            event.preventDefault();

            if (likeButton.disabled) {
                return;
            }

            const url = likeButton.dataset.url;

            if (!url) {
                return;
            }

            likeButton.disabled = true;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(function (response) {

                if (!response.ok) {
                    throw new Error("Like request failed.");
                }

                return response.json();

            })
            .then(function (data) {

                document.getElementById("like-icon").textContent =
                    data.liked ? "❤️" : "🤍";

                document.getElementById("like-text").textContent =
                    data.liked ? "Liked" : "Like";

                const countEl = document.getElementById("like-count");

                countEl.textContent =
                    data.like_count_display !== undefined
                        ? data.like_count_display
                        : data.like_count;

                countEl.title = data.like_count + " likes";

                likeButton.classList.toggle(
                    "liked",
                    data.liked
                );

            })
            .catch(function (error) {

                console.error("Like error:", error);

            })
            .finally(function () {

                likeButton.disabled = false;

            });

        });

    }


    /*
    =========================
    SHARE ARTICLE
    =========================
    */

    window.shareArticle = function () {

        const title = document.title;
        const url = window.location.href;

        if (navigator.share) {

            navigator.share({
                title: title,
                url: url
            }).catch(function () {
                // User cancelled sharing.
            });

            return;
        }

        if (navigator.clipboard) {

            navigator.clipboard.writeText(url)
                .then(function () {

                    alert(
                        "Article link copied to clipboard."
                    );

                })
                .catch(function () {

                    fallbackCopy(url);

                });

            return;
        }

        fallbackCopy(url);

    };


    /*
    =========================
    FALLBACK COPY
    =========================
    */

    function fallbackCopy(text) {

        const temporaryInput =
            document.createElement("input");

        temporaryInput.value = text;

        document.body.appendChild(
            temporaryInput
        );

        temporaryInput.select();

        document.execCommand("copy");

        document.body.removeChild(
            temporaryInput
        );

        alert(
            "Article link copied to clipboard."
        );

    }


    /*
    =========================
    CSRF COOKIE
    =========================
    */

    function getCookie(name) {

        let cookieValue = null;

        if (
            document.cookie &&
            document.cookie !== ""
        ) {

            const cookies =
                document.cookie.split(";");

            for (
                let i = 0;
                i < cookies.length;
                i++
            ) {

                const cookie =
                    cookies[i].trim();

                if (
                    cookie.substring(
                        0,
                        name.length + 1
                    ) === name + "="
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;

                }

            }

        }

        return cookieValue;

    }


    /*
    =========================
    BROKEN NEWS IMAGES
    =========================
    */

    const fallbackImage =
        "/static/newspulsehqapp/images/fallback-news.jpg";

    document
        .querySelectorAll("img")
        .forEach(function (image) {

            image.addEventListener(
                "error",
                function () {

                    if (
                        image.src.includes(
                            "fallback-news.jpg"
                        )
                    ) {
                        return;
                    }

                    image.src = fallbackImage;

                }
            );

        });

});