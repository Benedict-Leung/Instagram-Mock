$(document).ready(function () {
    $(".uploadImage").change(function() {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            
            reader.onload = function(e) {
                $(".preview .imageContainer img").attr("src", e.target.result);
                $(".preview .imageContainer img").removeAttr("alt");
            }
            
            reader.readAsDataURL(this.files[0]);
        }
    });
});