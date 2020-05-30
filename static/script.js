var player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('video-placeholder');
}

function highlight(videoId, startSeconds, endSeconds) {
    var vid = new String(videoId)
    player.loadVideoById({videoId:videoId, startSeconds:startSeconds, endSeconds:endSeconds});
}

