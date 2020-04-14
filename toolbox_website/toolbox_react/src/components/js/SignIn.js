import React, { Component } from 'react';
import "../css/Form.css";

/**
 * This component is the formular the user must fill to connect 
 * to his account.
 * @param 
 * @return 'XML form'  
 */
class SignIn extends Component {
    
    constructor(){
        super();

        this.state ={
            alias:'',
            email:'',
            password:''
        }
        
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(e) {
        let target = e.target;
        let value = target.type === 'checkbox' ? target.checked : target.value;
        let name = target.name;

        this.setState({
          [name]: value
        });
    }

    handleSubmit(e) {
        e.preventDefault();

        console.log('The form was submitted with the following data:');
        console.log(this.state);
    }

    render() {
        console.log("coucou");
        return (
            <>
            <form id="signInForm" onSubmit={this.handleSubmit}>
                <label className='FormField_Label' htmlFor='alias'>Alias :</label> 
                <input type='text' className='FormField_Input' name='alias' placeholder='Enter your alias' value={this.state.alias} onChange={this.handleChange}/>
            
                <label className='FormField_Label' htmlFor='email'>E-mail address </label> 
                <input type='email' className='FormField_Input' name ='email' placeholder='Enter your e-mail address' value={this.state.email} onChange={this.handleChange}/>
            
                <label className='FormField_Label' htmlFor='password'>Password </label> 
                <input type='password' className='FormField_Input' name ='password' placeholder='Enter your password' value={this.state.password} onChange={this.handleChange}/>
            </form>
            </>
        )
    }
}

export default SignIn