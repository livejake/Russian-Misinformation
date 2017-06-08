import React, { Component } from "react";
import moment from "moment";
import expandUrl from "./utils/expandUrl";
import TopNTable from "./components/TopNTable";

console.log("Top", TopNTable);

export default class Dashboard extends Component {
  constructor() {
    super();
    this.state = {
      tweetUrls: []
    };
  }

  getAllTweets = url => {
    return fetch(url)
      .then(response => response.json())
      .then(responseJson => {
        console.log("RESPONSE JSON: ", responseJson);
        return responseJson;
      })
      .catch(error => {
        alert("Turn on Python or check CORS!");
        console.error(error);
      });
  };

  filterByNDaysAgo = (daysAgo, data) => {
    // note follows strict url JSON structure
    const today = new Date();
    const yest = today.setDate(today.getDate() - daysAgo);
    const yesterday = moment(yest).format("YYYY/MM/DD");

    return data
      .filter(t => {
        const parsedTweetDate = Date.parse(t.created_at);
        const tweetDate = moment(parsedTweetDate).format("YYYY/MM/DD");
        return tweetDate === yesterday && t.urls.length > 0;
      })
      .map(t => t.urls.map(url => url.fully_expanded_url2));
  };

  urlFrequency = urls => {
    return urls.reduce((obj, str) => {
      if (obj[str[0]]) {
        obj[str[0]]++;
        return obj;
      } else {
        obj[str[0]] = 1;
        return obj;
      }
    }, {});
  };

  sortUrls = urls => {
    let sortable = [];
    for (let url in urls) {
      sortable.push([url, urls[url]]);
    }

    sortable.sort(function(a, b) {
      return b[1] - a[1];
    });

    return sortable;
  };

  getSortedAndFilteredBydateTweets = () => {
    this.getAllTweets("http://0.0.0.0:5000/")
      .then(tweets => {
        return this.filterByNDaysAgo(12, tweets);
      })
      .then(urls => {
        const urlCount = this.urlFrequency(urls);
        const sortedUrls = this.sortUrls(urlCount);
        this.setState({ tweetUrls: sortedUrls });
      });
  };

  componentDidMount = () => {
    this.getSortedAndFilteredBydateTweets();
  };

  render() {
    return (
      <div>
        <h1>Dashboard</h1>

        {this.state.tweetUrls.length > 0 &&
          <TopNTable data={this.state.tweetUrls} type="Url" amount={10} />}
      </div>
    );
  }
}
