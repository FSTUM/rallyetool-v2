//
//  ViewController.swift
//  Soundboard
//
//  Created by Matthias Linhuber on 12.10.18.
//  Copyright © 2018 Matthias Linhuber. All rights reserved.
//

import UIKit
import AVFoundation

class ViewController: UIViewController {
    var player: AVAudioPlayer?
    
    let defaultColor = UIColor.gray
    let highlightColor = UIColor.green
    
    var buttons = [UIButton?]()
    var songs = [SoundObject]()
    
    @IBOutlet weak var songButton1: UIButton!
    @IBOutlet weak var songButton2: UIButton!
    @IBOutlet weak var songButton3: UIButton!
    @IBOutlet weak var songButton4: UIButton!
    @IBOutlet weak var songButton5: UIButton!
    @IBOutlet weak var songButton6: UIButton!
    @IBOutlet weak var songButton7: UIButton!
    @IBOutlet weak var songButton8: UIButton!
    @IBOutlet weak var songButton9: UIButton!
    @IBOutlet weak var songButton10: UIButton!
    @IBOutlet weak var songButton11: UIButton!
    
    
    var sound1 = SoundObject(name: "Also-sprach-Zarathustra", artist: "Richard Strauss", fileName: "Also-sprach-Zarathustra", fileExtension: "wav")
    var sound2 = SoundObject(name: "Animals", artist: "Martin Garrix", fileName: "Animals", fileExtension: "wav")
    var sound3 = SoundObject(name: "bury a friend", artist: "Billie Eilish", fileName: "bury-a-friend", fileExtension: "m4a")
    var sound4 = SoundObject(name: "Immortals", artist: "Fall Out Boy", fileName: "Immortals", fileExtension: "m4a")
    var sound5 = SoundObject(name: "La La La", artist: "Naughty Boy", fileName: "La-La-La", fileExtension: "m4a")
    var sound6 = SoundObject(name: "Ni__as-in-Paris", artist: "JAY-Z & Kanye West", fileName: "Ni__as-in-Paris", fileExtension: "m4a")
    var sound7 = SoundObject(name: "Numb", artist: "Linkin Park", fileName: "Numb", fileExtension: "m4a")
    var sound8 = SoundObject(name: "Red Flag", artist: "Billy Talent", fileName: "Red-Flag", fileExtension: "mp3")
    var sound9 = SoundObject(name: "Say-Amen (Saturday Night)", artist: "Panic! At the Disco", fileName: "Say-Amen", fileExtension: "m4a")
    var sound10 = SoundObject(name: "Sing", artist: "Ed Sheeran", fileName: "Sing", fileExtension: "m4a")
    var sound11 = SoundObject(name: "The Next Episode", artist: "Dr Dre", fileName: "The-Next-Episode", fileExtension: "m4a")
    
    var selectedSound: SoundObject?
    
    @IBOutlet weak var TitleLabel: UILabel!
    @IBOutlet weak var artistLabel: UILabel!
    
    @IBAction func selectSong1(_ sender: Any) {
        changeSong(song: sound1)
        hightlightButton(buttonNumber: 1)
    }
    @IBAction func selectSong2(_ sender: Any) {
        changeSong(song: sound2)
        hightlightButton(buttonNumber: 2)
    }
    @IBAction func selectSong3(_ sender: Any) {
        changeSong(song: sound3)
        hightlightButton(buttonNumber: 3)
    }
    @IBAction func selectSong4(_ sender: Any) {
        changeSong(song: sound4)
        hightlightButton(buttonNumber: 4)
    }
    @IBAction func selectSong5(_ sender: Any) {
        changeSong(song: sound5)
        hightlightButton(buttonNumber: 5)
    }
    @IBAction func selectSong6(_ sender: Any) {
        changeSong(song: sound6)
        hightlightButton(buttonNumber: 6)
    }
    @IBAction func selectSong7(_ sender: Any) {
        changeSong(song: sound7)
        hightlightButton(buttonNumber: 7)
    }
    @IBAction func selectSong8(_ sender: Any) {
        changeSong(song: sound8)
        hightlightButton(buttonNumber: 8)
    }
    @IBAction func selectSong9(_ sender: Any) {
        changeSong(song: sound9)
        hightlightButton(buttonNumber: 9)
    }
    @IBAction func selectSong10(_ sender: Any) {
        changeSong(song: sound10)
        hightlightButton(buttonNumber: 10)
    }
    @IBAction func selectSong11(_ sender: Any) {
        changeSong(song: sound11)
        hightlightButton(buttonNumber: 11)
    }
    @IBAction func play1sec(_ sender: Any) {
        playAndPause(songLen: 1)
    }
    @IBAction func play3sec(_ sender: Any) {
        playAndPause(songLen: 3)
    }
    @IBAction func play5sec(_ sender: Any) {
        playAndPause(songLen: 5)
    }
    @IBAction func play10sec(_ sender: Any) {
        playAndPause(songLen: 10)
    }
    @IBAction func play30sec(_ sender: Any) {
        playAndPause(songLen: 30)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        buttons = [songButton1, songButton2, songButton3, songButton4, songButton5, songButton6, songButton7, songButton8, songButton9, songButton10, songButton11]
        songs = [sound1, sound2, sound3, sound4, sound5, sound6, sound7, sound8, sound9, sound10, sound11]
        
        for (button, song) in zip(buttons, songs) {
            button?.setTitle(song.name, for: .normal)
        }
        selectedSound = sound1
        TitleLabel.text = selectedSound?.name
        artistLabel.text = selectedSound?.artist
        songButton1.backgroundColor = UIColor.green
    }

    func playAndPause(songLen: Int) {
        if player == nil {
            play(len: songLen)
        }
        else {
            if player!.isPlaying {
                stop()
            }
            else {
                play(len: songLen)
            }
        }
    }
    
    func play(len: Int) {
        
        let path = Bundle.main.path(forResource: "\(len)-\(selectedSound!.fileName)", ofType : selectedSound?.fileExtension)!
        let url = URL(fileURLWithPath : path)
        
        do {
            player = try AVAudioPlayer(contentsOf: url)
            player!.play()

        } catch {
            
            print ("Play Failed")
            
        }
    }
    
    func stop()  {
        player!.stop()
    }
    
    func changeSong(song: SoundObject) {
        if player != nil {
            stop()
        }
        selectedSound = song
        TitleLabel.text = selectedSound?.name
        artistLabel.text = selectedSound?.artist
        print("Change to song \(song.name)")
    }
    
    func hightlightButton(buttonNumber: Int){
        for button in buttons {
            button?.backgroundColor = defaultColor
        }
        buttons[buttonNumber-1]?.backgroundColor = highlightColor
        
    }
    
    
}

