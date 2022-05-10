import React from 'react';
import PropTypes from 'prop-types';

class Modes extends React.Component {

    constructor(props) {
        super(props);
        this.state = { modes: {}, currentMode: '', currentSubMode: '', currentColor: '', enableColor: false, enableSubMode: false};

        this.handleModeChange = this.handleModeChange.bind(this);
        this.handleColorChange = this.handleColorChange.bind(this);
        this.handleSubModeChange = this.handleSubModeChange.bind(this);
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
                    currentSubMode: data.current_submode,
                    currentColor: data.current_color,
                    enableColor: data.modes[data.current_mode]['color'],
                    enableSubMode: (data.modes[data.current_mode]['submodes'].length !== 0)
                })
            })
            .catch((error) => console.log(error));
    }

    handleModeChange(event) {
        const { api } = this.props;
        const { modes, currentColor } = this.state;
        const {color, submodes } = modes[event.target.value]
        

        const stateUpdate = {
            currentMode: event.target.value,
            ...((submodes.length !== 0) && {currentSubMode: submodes[0]}),
            enableSubMode: (submodes.length !== 0),
            enableColor: color,
        }

        const message = {
            'mode': event.target.value,
            ...((submodes.length !== 0) && {'submode': submodes[0]}),
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
        const {currentMode, currentSubMode, enableSubMode } = this.state;

        const message = {
            'mode': currentMode,
            'color': event.target.value,
            ...(enableSubMode && {'submode': currentSubMode})
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

    handleSubModeChange(event) {
        const { api } = this.props;
        const {currentMode, currentColor, enableColor} = this.state;

        const message = {
            'mode': currentMode,
            'submode': event.target.value,
            ...(enableColor && {'color': currentColor})
        };

        fetch(api, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify(message)
        });

        this.setState({currentSubMode: event.target.value});
    }

    render() {
        const {currentMode, currentColor, currentSubMode, modes, enableColor, enableSubMode} = this.state;
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
                {enableSubMode &&
                    <div>
                        <label>
                            Secondary Modes: 
                            <select value={currentSubMode} onChange={this.handleSubModeChange}>
                                {modes[currentMode]['submodes'].map((mode) => (
                                    <option key={mode} value={mode}>{mode}</option>
                                ))}
                            </select> 
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