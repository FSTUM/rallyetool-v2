//
//  SoundObject.swift
//  Soundboard
//
//  Created by Dominic Henze on 24.09.19.
//  Copyright © 2019 Dominic Henze. All rights reserved.
//

import Foundation
import UIKit

struct SoundObject {
    
    let name: String
    let artist: String
    var image: UIImage?
    
    let fileURL: URL
    
    init(name: String, artist: String, fileName: String, fileExtension: String, imageName: String? = nil) {
        self.name = name
        self.artist = artist
        
        let path = Bundle.main.path(forResource: fileName, ofType : fileExtension)!
        self.fileURL = URL(fileURLWithPath : path)

        guard let imageName = imageName else {
            image = UIImage(systemName: Config.Master.Text.backupIcon, withConfiguration: UIImage.SymbolConfiguration(textStyle: .largeTitle))!
            return
        }
        
        image = UIImage(named: imageName)
    }
}
