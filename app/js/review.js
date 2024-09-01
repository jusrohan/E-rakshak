window.onload = function () {
  chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
    const hostname = new URL(tabs[0].url).hostname;
    fetch("http:/127.0.0.1:5000/reviews?url=" + hostname)
      .then((response) => {
        return response.text();
      })
      .then((html) => {
     
        console.log(html);
      });
  });
};
