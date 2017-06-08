import React from 'react'

/*

Pass data as an Array of items sorted by frequency
example: [['www.juicecrawl.com', 2], [etc...]]

 */

const TopNTable = ({ data, type, amount = 10 }) => {
    const limitedData = data.slice(0, amount)
    const items = limitedData.map(url => {
        return(
            <tr key={url}>
                <td><a href={url[0]}>{url[0]}</a></td>
                <td>{url[1]}</td>
            </tr>
        )
    })
        return (
                <table>
                    <thead>
                    <tr>
                        <th>{type}</th>
                        <th>Frequency</th>
                    </tr>
                    </thead>
                    <tbody>
                        {items}
                    </tbody>
                </table>
        )

}

export default TopNTable
