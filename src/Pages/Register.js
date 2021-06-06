import React, {useEffect} from 'react';

import {Header} from '../Components/Card/card';

import {Form} from '../Components/Forms/RegistrationForm';


export const Register = () => {
    useEffect( () => {
        fetch("/api/register").then(response => {
            if(response.ok)
                return response.json();
        })
        .then(
            data => console.log(data)
        )
    }, [])

    return(
        <>
            <Header />
            <h1>Register</h1>
            <Form></Form>
        </>
    )
}

export default Register;