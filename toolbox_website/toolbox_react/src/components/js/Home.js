import React from "react";
import "../css/Home.css";
import logo from "../../nut.svg";

export default function Home() {
  return (
    <div className="App">
      <section className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
      </section>
    </div>
  );
}