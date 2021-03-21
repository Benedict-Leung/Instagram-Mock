$("document").ready(function () {
    $(".register-title").fadeOut(0);
    $("#reenter-password-info").fadeOut(0);
    $(".login-link").fadeOut(0);
    $("#register-button").fadeOut(0);
    $(".register-info").fadeOut(0);

    $(".register").click(function () {
        $("#reenter-password").attr("required", true);
        $(".login-title, #username-info, #password-info, .register-link, #login-button, .message").fadeOut(0);
        $(".register-title, #username-info, #password-info, #reenter-password-info, #account-type, .login-link, .message").delay(450).fadeIn(500);
        $("#register-button").delay(450).fadeTo(300, 1);
        $(".login-form").attr("action", "/register");
        $(".form").css("transform", "rotateY(180deg)");
        $(".form-title img").css("transform", "rotateY(90deg)");

        setTimeout(function() {
            $(".form-title img").css("transform", "rotateY(180deg)");
        }, 250);

        setTimeout(function() {
            $(".form").css("transition", "all 0s");
            $(".form").css("transform", "rotateY(0)");
            $(".form-title img").css("transition", "all 0s");
            $(".form-title img").css("transform", "rotateY(0)");
            setTimeout(function() {
            $(".form-title img").css("transition", "all 0.25s linear");
            $(".form").css("transition", "all 0.5s linear");
            }, 100);
        }, 500);
        $(".form").css({height: "75vh"});
    });

    $(".login").click(function () {
        $(".register-title, #username-info, #password-info, #reenter-password-info, .register-info, .login-link, #register-button, .message").fadeOut(0);
        $(".login-title, #username-info, #password-info, .register-link, .message").delay(450).fadeIn(500);
        $("#reenter-password").attr("required", false);
        $("#login-button").delay(450).fadeTo(300, 1);
        $(".login-form").attr("action", "/login");
        $(".form").css("transform", "rotateY(180deg)");
        $(".form-title img").css("transform", "rotateY(90deg)");

        setTimeout(function() {
            $(".form-title img").css("transform", "rotateY(180deg)");
        }, 250);

        setTimeout(function() {
            $(".form").css("transition", "all 0s");
            $(".form").css("transform", "rotateY(0deg)");
            $(".form-title img").css("transition", "all 0s");
            $(".form-title img").css("transform", "rotateY(0)");
            setTimeout(function() {
            $(".form-title img").css("transition", "all 0.25s linear");
            $(".form").css("transition", "all 0.5s linear");
            }, 100);
        }, 500);
        $(".form").css({height: "55vh"});
    });
});
