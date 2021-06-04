import React, {useEffect} from 'react';

import {Card} from '../Components/Card/card';

import {Form} from '../Components/Forms/RegistrationForm';


export const Register = () => {
    useEffect( () => {
        fetch("/api/register").then(response => {
            if(response.ok)
                return response.json()
        }).then(data => console.log(data))
    }, [])
    
    
    return(
        <>
            <Form></Form>
            <Card></Card>
            <Form></Form>
            <Card></Card>
            <Form></Form>
        </>
    )
}

export default Register;