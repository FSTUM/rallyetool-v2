//
//  DemoData.swift
//  Soundboard
//
//  Created by Dominic Henze on 24.09.19.
//  Copyright © 2019 Dominic Henze. All rights reserved.
//

import Foundation

class SoundData {
    
    public static let shared = SoundData()
    
    public let mockData = [
        SoundObject(name: "Also sprach Zarathustra", artist: "Richard Strauss", fileName: "Also-sprach-Zarathustra", fileExtension: "wav", imageName: "AlsoSprachZarathustra"),
        SoundObject(name: "Animals", artist: "Martin Garrix", fileName: "Animals", fileExtension: "wav", imageName: "Animals"),
        SoundObject(name: "Bury a Friend", artist: "Billie Eilish", fileName: "bury-a-friend", fileExtension: "m4a", imageName: "BuryAFriend"),
        SoundObject(name: "Immortals", artist: "Fall Out Boy", fileName: "Immortals", fileExtension: "m4a", imageName: "Immortals"),
        SoundObject(name: "La La La", artist: "Naughty Boy", fileName: "La-La-La", fileExtension: "m4a", imageName: "Lalala"),
        SoundObject(name: "Ni__as in Paris", artist: "JAY-Z & Kanye West", fileName: "Ni__as-in-Paris", fileExtension: "m4a", imageName: "Ni__asInParis"),
        SoundObject(name: "Numb", artist: "Linkin Park", fileName: "Numb", fileExtension: "m4a", imageName: "Numb"),
        SoundObject(name: "Red Flag", artist: "Billy Talent", fileName: "Red-Flag", fileExtension: "mp3", imageName: "RedFlag"),
        SoundObject(name: "Say Amen (Saturday Night)", artist: "Panic! At the Disco", fileName: "Say-Amen", fileExtension: "m4a", imageName: "SayAmen"),
        SoundObject(name: "Sing", artist: "Ed Sheeran", fileName: "Sing", fileExtension: "m4a", imageName: "Sing"),
        SoundObject(name: "The Next Episode", artist: "Dr Dre", fileName: "The-Next-Episode", fileExtension: "m4a", imageName: "TheNextEpisode")
    ]
}
