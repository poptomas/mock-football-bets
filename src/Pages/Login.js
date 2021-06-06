import React, {useState, useEffect} from 'react';

import {Form} from '../Components/Forms/RegistrationForm';
import { LoginForm } from '../Components/Forms/LoginForm';
import { Card } from '../Components/Card/card';

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
        </>
    )
}

export default Login;
