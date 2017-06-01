import React, { Component } from 'react'
import moment from 'moment'
import expandUrl from './utils/expandUrl'

export default class Dashboard extends Component {

  getLatestTweets = () => {
    return fetch('http://0.0.0.0:5000/')
      .then((response) => response.json())
      .then((responseJson) => {
        console.log('RESPONSE JSON: ', responseJson)
        return responseJson
      })
      .catch((error) => {
        alert('Turn on Python or check CORS!')
        console.error(error);
      });
  }

  yesterdayTweetsWithUrls = () => {
    const today = new Date()
    const yest = today.setDate(today.getDate() - 12);
    const yesterday = moment(yest).format("YYYY/MM/DD")

    return this.getLatestTweets()
    .then(tweets => {
      return tweets.filter(t => {
        const parsedTweetDate = Date.parse(t.created_at)
        const tweetDate = moment(parsedTweetDate).format("YYYY/MM/DD")
        return tweetDate === yesterday && t.urls.length > 0
      })
      .map(t => t.urls.map(url => url.fully_expanded_url2))
    })
  }

  urlFrequency = (urls) => {
    return urls.reduce((obj, str) => {
      if(obj[str[0]]){
        obj[str[0]]++
        return obj
      }else{
        obj[str[0]] = 1
        return obj
      }
    }, {})
  }

  render() {
    const urls = this.yesterdayTweetsWithUrls()
    .then(urls => {
      console.log('RESULT HERE', this.urlFrequency(urls))
    })

    return (
      <div>
        <h1>Dashboard</h1>
      </div>
    )
  }
}
