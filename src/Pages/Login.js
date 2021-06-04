import React, {useState, useEffect} from 'react';

import {Card} from '../Components/Card/card';

import {Form} from '../Components/Forms/RegistrationForm';

export const Login = () => {
    
    const [todo, setTodo] = useState([]);

    useEffect( () => {
        fetch("/api/login").then(response => {
            if(response.ok)
                return response.json()
        }).then(data => console.log(data))
    }, [])
    
    
    return(
        <>
        <Card />
        </>
    )
}

export default Login;