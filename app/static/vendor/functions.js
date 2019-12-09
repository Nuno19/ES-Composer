function getImgFromServer(imdbID,START,size) {
    $.get("/getPoster", { imdbID: imdbID,size:size }, function (data) {
      $("#"+ START + imdbID).attr("src", data);
      console.log(data);
    });
  }

  function getBackDrop(imdbID,id) {
    $.get("/getBackDrop", { imdbID: imdbID}, function (data) {
     
      $("#"+id).css("background-image", "linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),url("+data+")");
      $("#"+id).css("background-size", "cover");
      
    });
  }

  function hideSpan(){
    $("#searchSpan").css("opacity","0");
  }
  function showSpan(){
    $("#searchSpan").css("opacity","1");
  }
  function setBackground(imdbID) {
    $.get("/getBackDrop", { imdbID: imdbID}, function (data) {
     console.log("BACKDROP")
     document.body.style.backgroundImage = "linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),url("+data+")";
     document.body.style.backgroundSize = "cover";
      
    });
   }