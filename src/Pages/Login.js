import React, {useState, useEffect} from 'react';

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
        </>
    )
}

export default Login;