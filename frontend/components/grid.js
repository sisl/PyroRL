import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import '../styles/grid.css'; // Create a new CSS file for custom styles (e.g., Grid.css)

const Grid = () => {
  const gridSize = 20;
  const generateRandomFloat = () => Math.random().toFixed(2);
  const opacities = Array.from({ length: 20 }, () => Array.from({ length: 20 }, generateRandomFloat));

  // Helper function to create an array of size `gridSize` and fill it with numbers from 1 to `gridSize`
  const createGridArray = () => {
    return Array.from({ length: gridSize }, (_, index) => index + 1);
  };

  return (
    <Container className="tic-tac-toe-grid">
      {createGridArray().map((rowIndex) => (
        <Row key={rowIndex}>
          {createGridArray().map((colIndex) => (
            <Col key={colIndex} className="square" style={{ opacity: opacities[rowIndex - 1][colIndex - 1] }}>
              {colIndex + (rowIndex - 1) * gridSize}
            </Col>
          ))}
        </Row>
      ))}
    </Container>
  );
};

export default Grid;
