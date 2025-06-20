# One Day Walking Simulator

A peaceful walking simulation game where you take a break from computer work to watch someone take a relaxing walk by the seaside.

![One Day Walking Simulator](screenshot.png)

## 🌟 Features

- **Immersive Room-to-Window Transition**: Experience standing up from your desk and walking to the window
- **Realistic Desktop PC Environment**: Detailed CRT monitor, keyboard, and room setup
- **Natural Walking Animation**: Smooth camera movement with walking bob effects
- **Persistent Window Frame**: Window cross remains visible throughout the transition
- **Time-of-Day Variations**: Different sky colors and lighting based on current time
- **Seasonal Changes**: Visual variations throughout the year
- **Customizable Duration**: Set walking time from 3 to 60 minutes
- **Retro CRT Interface**: Authentic green-screen computer terminal experience

## 🎮 How to Play

1. **Launch the Application**
   ```bash
   python3 one_day.py
   ```

2. **Set Walking Duration**
   - Click on the green input box on the CRT screen
   - Type a number between 3-60 (minutes)
   - Press Enter to start

3. **Experience the Transition**
   - Watch as you stand up from your chair (2 seconds)
   - Walk to the window with natural movement (4.4 seconds)
   - Focus on the window as it expands (1.6 seconds)
   - Enjoy the peaceful walking scene

4. **Restart**
   - Press 'R' when the walk is complete to return to the room

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- pygame library

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/one-day-walking-simulator.git
   cd one-day-walking-simulator
   ```

2. **Install dependencies**
   ```bash
   pip install pygame
   ```

3. **Run the application**
   ```bash
   python3 one_day.py
   ```

### Alternative: Using the run script

```bash
chmod +x run_one_day.sh
./run_one_day.sh
```

## 🎨 Technical Features

### Room Environment
- **Large Window**: 500x180 pixel window positioned behind CRT display
- **CRT Monitor**: 400x250 pixel retro computer screen with scan lines
- **Detailed Keyboard**: Realistic keyboard layout with individual keys (F1-F12, QWERTY, special keys)
- **Natural Lighting**: Room lighting adapts to time of day

### Transition System
- **8-Second Smooth Transition**: Carefully timed phases for natural movement
- **Walking Bob Animation**: Realistic up-down movement while walking
- **Adaptive Window Scaling**: Window grows smoothly while maintaining frame
- **Persistent Cross Frame**: Window dividers remain visible at all scales

### Walking Scene
- **Dynamic Sky**: Colors change based on real-world time
- **Seasonal Variations**: Different visual themes throughout the year
- **Character Animation**: Smooth walking animation with bounce effects
- **Progress Tracking**: Visual progress bar and timer display

## 🎯 Controls

- **Mouse**: Click CRT input box to activate
- **Keyboard**: Type numbers (3-60) for duration
- **Enter**: Start walking experience
- **R**: Restart (when walking is complete)
- **ESC**: Quit application

## 🔧 Configuration

The application automatically detects:
- Current time of day for appropriate sky colors
- Current season for visual variations
- Screen resolution for optimal display

## 📋 System Requirements

- **Operating System**: macOS, Windows, Linux
- **Python**: 3.7+
- **Memory**: 100MB RAM
- **Display**: Any resolution (optimized for 1440x240 and above)
- **Dependencies**: pygame 2.0+

## 🎨 Screenshots

### Room View
The initial room setup with CRT computer and large window behind.

### Transition Sequence
Smooth camera movement from desk to window with walking animation.

### Walking Scene
Peaceful seaside walking with dynamic sky and character animation.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for peaceful breaks during computer work
- Built with Python and pygame
- Designed for relaxation and mindfulness

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section below

### Troubleshooting

**Issue**: Application won't start
- **Solution**: Ensure Python 3.7+ and pygame are installed

**Issue**: Input box not responding
- **Solution**: Click directly on the green input box on the CRT screen

**Issue**: Window cross disappears during transition
- **Solution**: This has been fixed in the latest version - update to the newest release

## 🔄 Version History

- **v1.0.0**: Initial release with complete room-to-window transition system
- Features: 8-second transition, persistent window frame, detailed CRT interface

---

*Take a break, watch the walk, find your peace.* 🌊
