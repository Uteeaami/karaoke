import React, { useEffect, useState } from 'react';
import VideoPlayer from './components/videoPlayer';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [lang, setLang] = useState("");
  const [url, setUrl] = useState("");
  const [lyrics, setLyrics] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [processingTime, setProcessingTime] = useState(null);
  const [songs, setSongs] = useState([]);

  //Fetch song names that already exist and if true set its name and path to 'songs'-state variable
  useEffect(() => {
    fetch("/video")
      .then((response) => response.json())
      .then((data) => {
        const updatedSongs = data.song_names.map((name) => {
          return {
            name: name,
            videoPath: `/video/${name}`,
          };
        });
        setSongs(updatedSongs);
        console.log(updatedSongs)
      })
      .catch((error) => console.log(error));
  }, []);

  //Checks if the youtube URL is valid
  function isValidYoutubeUrl(url) {
    const youtubeUrlPattern = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    return youtubeUrlPattern.test(url);
  }

  //Runs the script to separate audio etc.. 
  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);                     //Parameter to track loading
    setProcessingTime(null);              //Parameter to track loading
    const startTime = performance.now();  //Parameter to track loading

    //Check yt URL
    if (!isValidYoutubeUrl(url)) {
      setLoading(false);
      setProcessingTime(null);
      setResult("Invalid YouTube URL");
      return;
    }

    //POST url and language to script function in FLASK
    const response = await fetch(`/script?lang=${encodeURIComponent(lang)}&url=${encodeURIComponent(url)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lyrics })
    });

    //Append the songs state with new song
    const text = await response.text();
    const [title, message] = text.split("|");
    const endTime = performance.now();                      //Parameter to track loading
    setResult(message);                                     //Get the 'Done' message
    setLoading(false);                                      //End loading prompt
    setProcessingTime(Math.round((endTime - startTime) / 1000));        //Get final time that the whole process took
    setSongs((prevSongs) => [...prevSongs, {name: title,videoPath: `/video/${encodeURIComponent(title)}`,},]);
  };
  
  //Formatting....below......
  return (
    <div className="container-fluid p-3">
      <div className="row justify-content-center">
        <div className="col-md-6 col-sm-12">
          <div className="card p-3">
            <h1 className="text-center">Karaoke</h1>
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
              <label htmlFor="lang" className="form-label">Language:</label>
              <select className="form-control" id="lang" value={lang} onChange={(e) => setLang(e.target.value)}>
                <option value="">Select a language</option>
                <option value="fi">Finnish</option>
                <option value="en">English</option>
              </select>
              </div>
              <div className="mb-3">
                <label htmlFor="url" className="form-label">YouTube URL:</label>
                <input type="text" className="form-control" id="url" value={url} onChange={(e) => setUrl(e.target.value)} />
              </div>
              <div className="mb-3">
                <label htmlFor="lyrics" className="form-label">Lyrics:</label>
                <textarea className="form-control" id="lyrics" rows="3" value={lyrics} onChange={(e) => setLyrics(e.target.value)} />
              </div>
              <div className="col-md-12 text-center">
                <button type="submit" className="btn btn-primary">Submit</button>
              </div>
            </form>
            <div className="mt-3 text-center fw-bold">
              {loading && <span className="text-warning">Processing...</span>}
              {result && !loading && (
                <span className="text-success">{result} {processingTime && <small>({processingTime} seconds)</small>}</span>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="row justify-content-center mt-3">
        {songs.map((song) => (
          <div className="col-md-2 col-sm-12 text-center" key={song.name}>
            <VideoPlayer videosrc={song.videoPath} videoname={song.name}></VideoPlayer>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
