import React, {useState, useEffect} from 'react';

<<<<<<< HEAD
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
=======
import { Card } from '../Components/Card/card';
import { LoginForm } from '../Components/Forms/LoginForm';

export const Login = () => {

    const url = "api/login";

    const [status, setStatus] = useState(null)

    useEffect(() => {
        fetch(url, {})
        .then(response => response.json())
        .then(json => {
            console.log(json)
            setStatus(json.status)
        })
    }, []);

    return(
        <>
        <Card />
        <LoginForm />
>>>>>>> api-flask-react
        </>
    )
}

export default Login;