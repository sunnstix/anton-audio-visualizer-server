import React from 'react';
import PropTypes from 'prop-types';

class Modes extends React.Component {

    constructor(props) {
        super(props);
        this.state = { modes: {}, currentMode: '', currentColor: '', enableColor: false};

        this.handleModeChange = this.handleModeChange.bind(this);
        this.handleColorChange = this.handleColorChange.bind(this);
    }

    componentDidMount() {
        const { api } = this.props;

        //  Update current and available modes from api
        fetch( api )
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({ 
                    modes: data.modes,
                    currentMode: data.current_mode,
                    currentColor: data.current_color,
                    enableColor: data.modes[data.current_mode]['color']
                })
            })
            .catch((error) => console.log(error));

        console.log(this.state)
    }

    handleModeChange(event) {
        const { api } = this.props;
        const { modes, currentColor } = this.state;
        const {color} = modes[event.target.value]
        

        const stateUpdate = {
            currentMode: event.target.value,
            enableColor: color,
        }

        const message = {
            'mode': event.target.value,
            ...((color) && {'color': currentColor})
        }

        fetch(api, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify(message)
        });

        this.setState(stateUpdate);
    }

    handleColorChange(event) {
        const { api } = this.props;
        const {currentMode} = this.state;

        const message = {
            'mode': currentMode,
            'color': event.target.value,
        };

        fetch(api, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify(message)
        });

        this.setState({currentColor: event.target.value});
    }

    render() {
        const {currentMode, currentColor, modes, enableColor,} = this.state;
        return (
            <div className = "mode_select">
                <div>
                    <label>
                        Light Modes: 
                        <select value={currentMode} onChange={this.handleModeChange}>
                            {Object.keys(modes).map((mode) => (
                                <option key={mode} value={mode}>{mode}</option>
                            ))}
                        </select> 
                    </label>
                </div>
                {enableColor &&
                    <div>
                        <label>
                            Color: 
                            <input type="color" value={currentColor} onChange={this.handleColorChange}></input>
                        </label>
                    </div>
                }
            </div>
        );
    }
};

Modes.propTypes = {
    api: PropTypes.string.isRequired,
};

export default Modes;