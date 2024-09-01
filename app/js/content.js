const endpoint = "http:/127.0.0.1:5000/";
const descriptions = {
  Sneaking:
    "Manipulates users to act in ways contrary to their usual behavior by concealing information. Covertly influences users to behave unexpectedly by withholding information.",

  Urgency:
    "Imparts a sense of immediacy to make items or actions seem more appealing. Introduces time constraints to create a perception of heightened desirability.",

  Misdirection:
    "Deceptively guides users toward a specific choice, diverting attention from alternatives. Influences user decisions by subtly steering them toward a particular option.",

  "Social Proof":
    "Creates the illusion that a particular action or product has garnered approval from others. Presents evidence, whether real or not, of widespread acceptance or endorsement.",

  Scarcity:
    "Elevates the perceived value of something by portraying it as limited in availability. Emphasizes the rarity or exclusivity of a product or service.",

  Obstruction:
    "Introduces obstacles to make an action more difficult, discouraging user engagement.",

  "Forced Action":
    "Compels users to complete extra, unrelated tasks to perform a seemingly simple action.",
};

function scrape() {


  // website has already been analyzed
  if (document.getElementById("insite_count")) {
    return;
  }
  const htmlSourceCode = document.documentElement.outerHTML;
  console.log(htmlSourceCode);
  // aggregate all DOM elements on the page
  let elements = segments(document.body);
  let filtered_elements = [];

  for (let i = 0; i < elements.length; i++) {
    let text = elements[i].innerText.trim().replace(/\t/g, " ");
    if (text.length == 0) {
      continue;
    }
    filtered_elements.push(text);
  }
 
 



  // post to the web server
  fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tokens: filtered_elements }),
  })
    .then((resp) => resp.json())
    .then((data) => {
      data = data.replace(/'/g, '"');
      json = JSON.parse(data);
      let dp_count = 0;
      let element_index = 0;

      for (let i = 0; i < elements.length; i++) {
        let text = elements[i].innerText.trim().replace(/\t/g, " ");
        if (text.length == 0) {
          continue;
        }

        if (json.result[i] !== "Not Dark") {
          highlight(elements[element_index], json.result[i]);
          dp_count++;
        }
        element_index++;
      }

      // store number of dark patterns
      let g = document.createElement("div");
      g.id = "insite_count";
      g.value = dp_count;
      g.style.opacity = 0;
      g.style.position = "fixed";
      document.body.appendChild(g);
      sendDarkPatterns(g.value);
    })
    .catch((error) => {
      alert(error);
      alert(error.stack);
    });
}



function highlight(element, type) {
  if (typeof (type) !== "undefined") {
    element.classList.add("insite-highlight");

    let body = document.createElement("span");
    body.classList.add("insite-highlight-body");

    /* header */
    let header = document.createElement("div");
    header.classList.add("modal-header");
    let headerText = document.createElement("h1");
    headerText.innerHTML = type + " Pattern";
    header.appendChild(headerText);
    body.appendChild(header);

    /* content */
    let content = document.createElement("div");
    content.classList.add("modal-content");

    content.innerHTML = descriptions[type];
    body.appendChild(content);

    element.appendChild(body);
  }
}

function sendDarkPatterns(number) {
  chrome.runtime.sendMessage({
    message: "update_current_count",
    count: number,
  });
}

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.message === "analyze_site") {
    scrape();
  } else if (request.message === "popup_open") {
    let element = document.getElementById("insite_count");
    if (element) {
      sendDarkPatterns(element.value);
    }
  }
});



