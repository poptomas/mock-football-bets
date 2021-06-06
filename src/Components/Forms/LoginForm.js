import React, {useState} from 'react'

export const LoginForm = () => {

    const [state, setState] = useState({username : "", password : ""})
  
    const handleChange = event => {
        const value = event.target.value
         setState({
            ...state,
            [event.target.name] : value
        });
    }
  
    const handleSubmit = event => {
        event.preventDefault();
        //console.log(this.state)
        const request = {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                username : state.username,
                password : state.password
            })
        };

        fetch("api/login", request)
            .then(response => 
                response.json())
            .then(json => {
                setState({
                    userData : json
                })
            })
            .catch( () => {
                console.log("Error happened meanwhile")
            })
    }
  
    return (
            <form onSubmit={handleSubmit}>
            <label>
                Name:
                <input type="text" value={state.username || ""} name = "username" onChange={handleChange} autoComplete="on" required />
            </label>
            <label>
                Password:
                <input type="password" value={state.password || ""} name = "password" onChange={handleChange} autoComplete="off" required />
            </label>
            <input type="submit" value="Submit" />
            </form>
    )
}