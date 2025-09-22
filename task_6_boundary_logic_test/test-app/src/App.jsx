import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const[username, setusername] = useState('')
  const[result, setResult] = useState(null)

  const validate =(e)=>{
     const input = username || ""
  // Boundary validation rules
  if (/^[A-Za-z0-9_-]*$/.test(input)){
    if (input.length < 3) {
    setResult("Error: Username must be at least 3 characters long")
  } else if (input.length > 20) {
    setResult("Error: Username must not exceed 20 characters.");
  } else {
    setResult("no error")
  }
  }
  else{
    setResult("Username must be letters and numbers")
  }
  
  }

  const handlechange = (e)=>{
    e.preventDefault()
    setusername(e.target.value.trim())
  }

  return (
    <div>
      {result && <div>{result}</div>}
      <input name='username'
      value={username}
      onChange={handlechange}
      placeholder='Enter username'
      ></input>
      <button onClick={validate}>Submit</button>
    </div>
  )
}

export default App
