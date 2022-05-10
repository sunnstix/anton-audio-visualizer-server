import React from 'react';
import ReactDom from 'react-dom';
import Modes from './mode_selector'

ReactDom.render(
    <Modes api='/api/modes/'/>,
    document.getElementById('mode-selector')
)