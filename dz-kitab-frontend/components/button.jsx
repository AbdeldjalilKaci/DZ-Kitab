import React from 'react'

export const Button = ({text,color,width,height,bordercolor,borderadius,backgroundcolor}) => {
    return (
        <button className='.button' style={{width:width,height:height,color:color,borderRadius:borderadius,backgroundColor:backgroundcolor,borderColor:bordercolor}}>
            {text}
        </button>
    )
}
