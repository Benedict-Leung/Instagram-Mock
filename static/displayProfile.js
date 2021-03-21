$(document).ready(function () {
    let follow = $(".follow").text() == "Unfollow";
    let requestSent = $(".follow").text() == "Request Sent";
    let profileName = $(".profileName").text();
    let username = $(".username").text();

    $(".follow").click(function () {
        let a = $(this)
        
        if (!a.hasClass("disabled")) {
            a.addClass("disabled")

            if (!follow && !requestSent) {
                $.ajax({
                    url: "/follow",
                    type: "POST",
                    data: {
                        profileName: profileName,
                        username: username
                    },
                    success: function(r) {
                        if (r == "Request Sent") {
                            requestSent = true;
                        } else {
                            follow = true;
                        }
                        a.removeClass("disabled");
                        a.text(r);
                    }
                });
            } else if (follow) {
                $.ajax({
                    url: "/unfollow",
                    type: "POST",
                    data: {
                        profileName: profileName,
                        username: username
                    },
                    success: function(r) {
                        follow = false;
                        a.removeClass("disabled");
                        a.text(r);
                    }
                });
            } else {
                $.ajax({
                    url: "/removeRequest",
                    type: "POST",
                    data: {
                        profileName: profileName,
                        username: username
                    },
                    success: function(r) {
                        requestSent = false
                        a.removeClass("disabled");
                        a.text(r);
                    }
                });
            }
        }
    });
});