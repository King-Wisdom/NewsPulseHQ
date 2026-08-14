document.addEventListener("DOMContentLoaded", function () {
    console.log("NewsPulseHQ loaded successfully.");

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

                document.getElementById("like-count").textContent =
                    data.like_count;

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
                    alert("Article link copied to clipboard.");
                })
                .catch(function () {
                    fallbackCopy(url);
                });

            return;
        }

        fallbackCopy(url);
    };


    function fallbackCopy(text) {
        const temporaryInput = document.createElement("input");

        temporaryInput.value = text;

        document.body.appendChild(temporaryInput);

        temporaryInput.select();

        document.execCommand("copy");

        document.body.removeChild(temporaryInput);

        alert("Article link copied to clipboard.");
    }


    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();

                if (
                    cookie.substring(0, name.length + 1) ===
                    name + "="
                ) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }
});