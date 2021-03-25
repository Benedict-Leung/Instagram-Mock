$(document).ready(function () {
    window.location.replace("/addPost#uploadContainer");

    var stream = document.getElementById("stream");
    var capture = document.getElementById("capture");
    var snapshot = document.getElementById("snapshot");

    var cameraStream = null;
    var started = false;
    let takenPhoto = false;

    $("#uploadButton").click(function () {
        $(this).addClass("active");
        $("#takeButton").removeClass("active");

        if (cameraStream != null) {
            var track = cameraStream.getTracks()[0];
            track.stop();
            stream.load();
            cameraStream = null;
            started = false;
            $(".cameraButton").text("Start Camera");
        }
    });

    $("#takeButton").click(function () {
        $(this).addClass("active");
        $("#uploadButton").removeClass("active");
    }); 

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

    $(".cameraButton").click(function() {
        if (!started) {
            let a  = $(this)
            var mediaSupport = "mediaDevices" in navigator;

            if (mediaSupport && null == cameraStream) {
                navigator.mediaDevices.getUserMedia({video: true, audio: false})
                .then(function(mediaStream) {
                    cameraStream = mediaStream;
                    stream.srcObject = mediaStream;
                    stream.play();
                    $(stream).css("display", "block");
                    $(snapshot).css("display", "none");
                    a.text("Take photo");
                    started = true;
                    takenPhoto = false;
                }).catch(function(err) {
                    console.log("Unable to access camera: " + err);
                });
            }
        } else {
            if (cameraStream!= null) {
                capture.width = $(stream).width();
                capture.height = $(stream).height();
                var ctx = capture.getContext("2d");
                var img = new Image();
    
                ctx.drawImage(stream, 0, 0, capture.width, capture.height);
            
                img.src = capture.toDataURL("image/png");
                $(img).attr("name", "image");
    
                snapshot.innerHTML = "";
                snapshot.appendChild(img);

                if (cameraStream != null) {
                    var track = cameraStream.getTracks()[0];
                    track.stop();
                    stream.load();
                    cameraStream = null;
                }
                $(stream).css("display", "none");
                $(snapshot).css("display", "block");
                $(this).text("Retake photo");
                started = false;
                takenPhoto = true;
            }
        }
    });

    $(".cameraSubmit").click(function () {
        if (takenPhoto) {
            var request = new XMLHttpRequest();

            request.open( "POST", "/addPost", true );

            var data	= new FormData();
            var dataURI	= snapshot.firstChild.getAttribute( "src" );
            var imageData   = dataURItoBlob( dataURI );

            data.append("image", imageData);
            data.append("caption", $(this).parent().find(".caption").val());
            request.send(data);
            window.location.replace("/displayProfile");
        }
    });
});

function dataURItoBlob( dataURI ) {
	var byteString = atob( dataURI.split( ',' )[ 1 ] );
	var mimeString = dataURI.split( ',' )[ 0 ].split( ':' )[ 1 ].split( ';' )[ 0 ];
	
	var buffer	= new ArrayBuffer( byteString.length );
	var data	= new DataView( buffer );
	
	for( var i = 0; i < byteString.length; i++ ) {
		data.setUint8( i, byteString.charCodeAt( i ) );
	}
	
	return new Blob( [ buffer ], { type: mimeString } );
}