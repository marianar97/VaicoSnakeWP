(function () {

    
    photo = document.getElementById('photo')
    

    document.getElementById('capture').addEventListener('click', function () {
        context.drawImage(video, 0, 0, 400, 300);
        photo.setAttribute('src', canvas.toDataURL('image/png'));
        // create_img();

    });


})();


function sendImage() {
    //Make this url, in a different file, so can be accessed from everywhere
    const url = "http://localhost:8000/saveImage";

    img = document.getElementById('photo');
    returned_image = document.getElementById('returned_photo');
    returned_image.src = './output.jpeg'
    
    // fetch(url, {
    //     method: "POST",
    //     body: JSON.stringify(img.src),
    //     headers: {
    //         'Content-Type': 'application/json',

    //     }
    // }).then(res => res.json())
    //     .catch(error => console.error('Error:', error))
    //     .then(response => {
    //         console.log('Success:', response);
    //         returned_image.src = './output.jpeg';
    //     });
    
}

function previewFile() {
    var preview = document.querySelector('img');
    var file = document.querySelector('input[type=file]').files[0];
    var reader = new FileReader();

    reader.onloadend = function () {
        photo.setAttribute('src', reader.result);

    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = "";
    }
}