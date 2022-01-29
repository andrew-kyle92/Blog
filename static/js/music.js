const playPauseBtn = document.getElementById("play-pause-btn");
const backBtn = document.getElementById("back-btn");
const forwardBtn = document.getElementById("forward-btn");
const volumeUpBtn = document.getElementsByClassName("fa-volume-up");
const volumeDownBtn = document.getElementsByClassName("fa-volume-off");
var currentTrackInfo = document.getElementsByClassName("track-info")[0];
var progressBar = document.getElementsByClassName("seek_slider")[0];
var volumeBar = document.getElementsByClassName("volume_slider")[0];
var songItem = document.getElementsByClassName("song-item");
var songs = document.getElementsByClassName("lower-level-tab");
var songImg = document.getElementsByClassName("song-img")[0];
var songObjects = {};
var songPlaying = false;

for(let i = 0; i < songs.length; i++){
    let json = songs [i].dataset.song;
    data = JSON.parse(json);
    song = {
        "id": data.id,
        "Artist": data.artist,
        "Song": data.song_name,
        "Album Art": data.artwork,
        "Song File": data.song_file
    }
    songObjects[data.id] = song;
}

function setTrack(s, track_id){
    songImg.setAttribute("src", s[track_id]["Album Art"]);
    duration = document.getElementsByClassName("seconds-start")[0];
    currentTrackInfo.innerText = s[track_id]["Artist"] + " - " + s[track_id]["Song"];
    currentTrack = new Audio(s[track_id]["Song File"]);
    currentTrack.id = parseInt(s[track_id]["id"]);
    songPlaying = true;
    s = parseInt(currentTrack.currentTime % 60);
    m = parseInt((currentTrack.currentTime / 60) % 60);
    if(s < 10){
        duration.innerText = m + ":0" + s;
    }
    else{
        duration.innerText = m + ":" + s;
    }
    endDuration = document.getElementsByClassName("seconds-end")[0];
    songDurationM = parseInt((currentTrack.duration / 60) % 60);
    songDurationS = parseInt(currentTrack.duration % 60)
    if(songDurationS < 10){
        endDuration.innerText = songDurationM + ":0" + songDurationS;
    }
    else{
        endDuration.innerText = songDurationM + ":" + songDurationS;
    }

    updateTime();

    for(let i = 0; i < songItem.length; i++){
        if(songItem[i].dataset["songId"] == track_id){
            songItem[i].setAttribute("class", "song-item song-playing");
        }
    }

    return currentTrack
}

var currentTrack = setTrack(songObjects, songObjects["1"]["id"]);

playPauseBtn.addEventListener("click", function(){
    if(playPauseBtn.className == "fas fa-play-circle"){
        songPlaying = true;
        playPauseBtn.setAttribute("class", "fas fa-pause-circle");
        currentTrack.play();
    }
    else{
        playPauseBtn.setAttribute("class", "fas fa-play-circle");
        songPlaying = false;
        currentTrack.pause();
    }
});

backBtn.addEventListener("click", function(){
    if(parseInt(currentTrack.id) > 0){
        previousTrack = parseInt(currentTrack.id) - 1;
    }
    else{
        previousTrack = parseInt(songObjects.at(-1)["id"]);
    }

    if(currentTrack.currentTime < 5){
        currentTrack.currentTime = currentTrack.duration;
        playPauseBtn.setAttribute("class", "fas fa-play-circle");
        songItem[parseInt(currentTrack.id)].setAttribute("class", "song-item");
        if(previousTrack == 0){
            setTrack(songObjects, songObjects.at(-1)["id"]);
        }
        else{
            setTrack(songObjects, previousTrack);
        }
    }
    else{
        currentTrack.currentTime = 0;
    }
});

forwardBtn.addEventListener("click", function(){
    currentTrack.currentTime = currentTrack.duration;
    playPauseBtn.setAttribute("class", "fas fa-play-circle");
    songItem[parseInt(currentTrack.id)].setAttribute("class", "song-item");
    if(parseInt(currentTrack.id) < songObjects.length - 1){
        currentTrack = setTrack(songObjects, songObjects[parseInt(currentTrack.id) + 1]["id"]);
        currentTrack.play();
        playPauseBtn.setAttribute("class", "fas fa-pause-circle");
    }
    else{
        currentTrack = setTrack(songObjects, songObjects[0]["id"]);
        currentTrack.play();
        playPauseBtn.setAttribute("class", "fas fa-pause-circle");
    }
});

function seekTo(){
    seek_to = currentTrack.duration * (progressBar.value / 100);
    currentTrack.currentTime = seek_to;
}

function setVolume() {
  // Set the volume according to the
  // percentage of the volume slider set
  currentTrack.volume = volumeBar.value / 100;
}

function updateTime(){
    currentTrack.addEventListener("timeupdate", function(){
        if(currentTrack.ended){
            currentTrack.currentTime = 0;
            songPlaying = false;
            playPauseBtn.setAttribute("class", "fas fa-play-circle");
        }
        else{
            duration = document.getElementsByClassName("seconds-start")[0];
            s = parseInt(currentTrack.currentTime % 60);
            m = parseInt((currentTrack.currentTime / 60) % 60);
            if(s < 10){
                duration.innerText = m + ":0" + s;
            }
            else{
                duration.innerText = m + ":" + s;
            }
        }
    });

    currentTrack.addEventListener("timeupdate", function(){
        endDuration = document.getElementsByClassName("seconds-end")[0];
        songDurationM = parseInt((currentTrack.duration / 60) % 60);
        songDurationS = parseInt(currentTrack.duration % 60)
        if(songDurationS < 10){
            endDuration.innerText = songDurationM + ":0" + songDurationS;
        }
        else{
            endDuration.innerText = songDurationM + ":" + songDurationS;
        }
    });

    currentTrack.addEventListener("timeupdate", function(){
        if(currentTrack.ended){
            sliderProgress = 0;
        }
        else{
            sliderValue = parseInt(progressBar.value);
            sliderProgress = progressBar.value = currentTrack.currentTime * (100 / currentTrack.duration);
        }
    });
};

function playTrack(song_id){
    if(songPlaying){
        currentTrack.currentTime = currentTrack.duration;
        songPlaying = false;
        for(let i = 0; i < songItem.length; i++){
            if(songItem[i].dataset["songId"] == currentTrack.id){
                songItem[i].setAttribute("class", "song-item");
            }
        }
        playPauseBtn.setAttribute("class", "fas fa-play-circle");
    }
    currentTrack = setTrack(songObjects, songObjects[song_id]["id"]);
    currentTrack.play();
    playPauseBtn.setAttribute("class", "fas fa-pause-circle");
};

function volumeUp(){
    if(volumeBar.value < 100){
        currentTrack.volume = currentTrack.volume + 0.05;
        volumeBar.value = parseInt(volumeBar.value) + 5;
    }
};

function volumeDown(){
    if(volumeBar.value > 0){
        currentTrack.volume = currentTrack.volume - 0.05;
        volumeBar.value = parseInt(volumeBar.value) - 5;
    }
};

// Artist List Functions
var artistBtn = document.getElementsByClassName("artist-btn")
var artistTabs = document.getElementsByClassName("artist-tab");
var albumTabs = document.getElementsByClassName("album-tab");
var songTabs = document.getElementsByClassName("song-tab");

for(let i = 0; i < artistBtn.length; i++){
    artistBtn[i].addEventListener("click", function(){
        content = this.nextElementSibling;
        if(content.style.display == "block"){
            content.style.display = "none";
        }
        else{
            content.style.display = "block";
        }
    });
}

for(let i = 0; i < artistTabs.length; i++){
    artistTabs[i].addEventListener("click", function(){
        content = this.nextElementSibling;
        if(content.style.display == "block"){
            content.style.display = "none";
            this.children[0].setAttribute("class", "fas fa-chevron-up");
        }
        else{
            content.style.display = "block";
            this.children[0].setAttribute("class", "fas fa-chevron-down");
        }
    });
}

for(let i = 0; i < albumTabs.length; i++){
    albumTabs[i].addEventListener("click", function(){
        content = this.nextElementSibling;
        if(content.style.display == "block"){
            content.style.display = "none";
            this.children[0].setAttribute("class", "fas fa-chevron-up");
        }
        else{
            content.style.display = "block";
            this.children[0].setAttribute("class", "fas fa-chevron-down");
        }
    });
}
