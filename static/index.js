$(document).ready(function () {
    let username = $(".username").text()

    $(".searchBar").on("keyup",function () {
        if ($(this).val() != "") {
            $.ajax({
                url: "/search",
                type: "POST",
                data: {username: $(this).val()},
                success: function(response) {
                    let results = $("<div class = 'searchResults'></div>")
                    
                    $(".searchResults").remove();
                    if (response.length != 0) {
                        for (let username of response) {
                            let label = $(`<label>${username}</label>`)
                            label.click(function () {
                                $.ajax({
                                    url: "/displayProfile",
                                    type: "POST",
                                    data: {username: username},
                                    success: function(r) {
                                        $("body").html(r)
                                    }
                                });
                            });
                            results.append(label);
                        }
                    } else {
                        let label = $("<label>No results</label>");
                        results.append(label);
                    }
                    
                    $(".header").append(results);
                }
            });
        } else {
            $(".searchResults").remove();
        }
    });

    $(".fa-heart").click(function () {
        let a = $(this);
        let id = $(this).parent().parent().attr("id");
        let color = $(this).css("color");

        if (String(color) == "rgb(0, 0, 0)") {
            $(this).css("color", "red");

            if (!a.hasClass("disbaled")) {
                a.addClass("disabled");
                $.ajax({
                    url: "/addLike",
                    type: "POST",
                    data: {id: id},
                    success: function() {
                        a.removeClass("disabled");
                    }
                });
            }
            
        } else {
            $(this).css("color", "black");

            if (!a.hasClass("disabled")) {
                a.addClass("disabled");
                $.ajax({
                    url: "/removeLike",
                    type: "POST",
                    data: {id: id},
                    success: function() {
                        a.removeClass("disabled");
                    }
                });
            }
        }
    });

    $(".fa-comment").click(function () {
        if ($(this).parent().parent().find(".newComment").length == 0) {
            let a = $(this).parent().parent()
            let id = a.attr("id");
            let newComment = $("<input class = 'newComment' placeholder = 'Add comment'></input>");
            $(this).parent().parent().append(newComment);
            
            newComment.on("keyup", function(e) {
                if (e.key === "Enter") {
                    $.ajax({
                        url: "/addComment",
                        type: "POST",
                        data: {
                            id: id,
                            comment: String(newComment.val())
                        }, success: function(response) {
                            newComment.remove();
                            a.append(response);
                        }
                    });
                }
            });
        }
    });

    $(".acceptRequest").click(function () {
        let a = $(this)
        
        if (!a.hasClass("disabled")) {
            a.addClass("disabled");
            $.ajax({
                url: "/acceptRequest",
                type: "POST",
                data: {
                    profileName: username,
                    username: a.attr("id")
                },
                success: function() {
                    a.parent().remove();
                }
            })
        }
    });
});
