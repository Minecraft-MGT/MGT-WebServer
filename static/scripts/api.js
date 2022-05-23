async function apiRequest(payload) {
    let res = await fetch("/api/", {method: "POST", body: JSON.stringify(payload)});
    let output = await res.json();
    console.log("API('"+JSON.stringify(payload)+"') --> "+String(JSON.stringify(output)));
    return output;
}
