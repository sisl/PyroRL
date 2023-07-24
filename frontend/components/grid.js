import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import '../styles/grid.css'; // Create a new CSS file for custom styles (e.g., Grid.css)

const Grid = () => {
  return (
    <Container className="tic-tac-toe-grid">
      <Row>
        <Col className="square">1</Col>
        <Col className="square">2</Col>
        <Col className="square">3</Col>
      </Row>
      <Row>
        <Col className="square">4</Col>
        <Col className="square">5</Col>
        <Col className="square">6</Col>
      </Row>
      <Row>
        <Col className="square">7</Col>
        <Col className="square">8</Col>
        <Col className="square">9</Col>
      </Row>
    </Container>
  );
};

export default Grid;
