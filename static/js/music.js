const playPauseBtn = document.getElementById("play-pause-btn");
const backBtn = document.getElementById("back-btn");
const forwardBtn = document.getElementById("forward-btn");
var currentTrackInfo = document.getElementsByClassName("track-info")[0];
var progressBar = document.getElementsByClassName("seek_slider")[0];
var volumeBar = document.getElementsByClassName("volume_slider")[0];
var songItem = document.getElementsByClassName("song-item");
var songs = document.getElementsByTagName("article");
var songImg = document.getElementsByClassName("song-img")[0];
var songObjects = {"songs": []};
var songPlaying = false;

for(let i = 0; i < songs.length; i++){
    song = {
        "id": i,
        "Artist": songs[i].dataset.songArtist,
        "Song": songs[i].dataset.songName,
        "Album Art": songs[i].dataset.songArtwork,
        "Song File": songs[i].dataset.songFile
    }
    songObjects["songs"].push(song);
}

songObjects = songObjects["songs"];

function setTrack(songs, track_id){
    songImg.setAttribute("src", songs[track_id]["Album Art"]);
    duration = document.getElementsByClassName("seconds-start")[0];
    currentTrackInfo.innerText = songs[track_id]["Artist"] + " - " + songs[track_id]["Song"];
    currentTrack = new Audio(songs[track_id]["Song File"]);
    currentTrack.id = songs[track_id]["id"];
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

    songItem[parseInt(currentTrack.id)].setAttribute("class", "song-item song-playing");

    return currentTrack
}

var currentTrack = setTrack(songObjects, songObjects[0]["id"]);

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
    currentTrack.currentTime = 0;
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
        songItem[parseInt(currentTrack.id)].setAttribute("class", "song-item");
        playPauseBtn.setAttribute("class", "fas fa-play-circle");
    }
    currentTrack = setTrack(songObjects, parseInt(song_id));
    currentTrack.play();
    playPauseBtn.setAttribute("class", "fas fa-pause-circle");
};