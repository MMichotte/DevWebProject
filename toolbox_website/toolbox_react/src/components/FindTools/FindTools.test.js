import React from "react";
import ReactDOM from "react-dom";
import FindTools from "./FindTools.js";
import TestRenderer from "react-test-renderer";
it("render without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(<FindTools />, div);
});

/*
Test de la snapshot (a faire que si le component ne bouge pas trop dans le temps)
Ce test ajoute un dossier _snaphsot_dans lequel est contenu toutes les snapshots
*/
it("renders a form", () => {
  const testRenderer = TestRenderer.create(<FindTools />);
  const testInstance = testRenderer.toJSON();
  expect(testInstance).toMatchSnapshot();
});
