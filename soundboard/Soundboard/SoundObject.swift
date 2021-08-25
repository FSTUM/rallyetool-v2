//
//  SoundObject.swift
//  Soundboard
//
//  Created by Matthias Linhuber on 12.10.18.
//  Copyright © 2018 Matthias Linhuber. All rights reserved.
//

import Foundation

class SoundObject {
    
    let name: String
    let artist: String
    
    let fileName: String
    
    let fileExtension: String
    
    init(name: String, artist: String, fileName: String, fileExtension: String) {
        self.name = name
        self.artist = artist
        self.fileName = fileName
        self.fileExtension = fileExtension
    }
}
