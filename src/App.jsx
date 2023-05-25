import { useEffect, useState } from 'react'
import { API } from 'aws-amplify'



function App () {
  useEffect(() => {
    const getData = async () => {
    const data = await API.get('seoautoapi', '/items')
//         const data = await API.post('seoautoapi','/items', {
//             body: {
//
//                 username: 'check6@gmail.com',
//                 password: 'qazws2503',
//                 user_id: '123456'
//             }
//         })

      console.log(data)
      }
      getData()
    })
  return <div></div>
  }

export default App






