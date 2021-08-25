//
//  StaticValues.swift
//  Soundboard
//
//  Created by Dominic Henze on 24.09.19.
//  Copyright © 2019 Dominic Henze. All rights reserved.
//

import Foundation
import UIKit

struct Config {
    
    // Defines which seconds are available on the buttons
    static let buttonTimeArrayInSeconds = [1, 2, 5, 15, 30, 45]
    
    struct Master {
        struct Color {
            static let barColor = #colorLiteral(red: 0.1897519529, green: 0.4373658299, blue: 0.7030764222, alpha: 1)
            static let barTextColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
            
            static let backgroundColor = #colorLiteral(red: 0.1686044633, green: 0.1686406434, blue: 0.1686021686, alpha: 1)
            
            static let cellBackgroundColor = #colorLiteral(red: 0.1686044633, green: 0.1686406434, blue: 0.1686021686, alpha: 1)
            static let cellTextColor = #colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)
            static let cellDetailTextColor = #colorLiteral(red: 0.6666666865, green: 0.6666666865, blue: 0.6666666865, alpha: 1)
            static let cellHighlightColor = #colorLiteral(red: 0.4744554758, green: 0.4745410681, blue: 0.4744500518, alpha: 1)
            static let cellBackupIcon = #colorLiteral(red: 1, green: 0.6627451181, blue: 0.07843137532, alpha: 1)
        }
        
        struct Text {
            static let barText = "Music Library"
            static let backupIcon = "music.note"
        }
    }
    
    struct Detail {
        struct Color {
            static let barColor = #colorLiteral(red: 0.1897519529, green: 0.4373658299, blue: 0.7030764222, alpha: 1)
            static let barTextColor = #colorLiteral(red: 1.0, green: 1.0, blue: 1.0, alpha: 1.0)
            
            static let backgroundColor = #colorLiteral(red: 0.1686044633, green: 0.1686406434, blue: 0.1686021686, alpha: 1)
            
            static let buttonColor = #colorLiteral(red: 0.1163601056, green: 0.1383497119, blue: 0.2544969022, alpha: 1)
            static let buttonHighlightColor = #colorLiteral(red: 1, green: 0.6627451181, blue: 0.07843137532, alpha: 1)
            static let buttonTextColor = #colorLiteral(red: 1.0, green: 1.0, blue: 1.0, alpha: 1.0)
            static let buttonBorderColor = #colorLiteral(red: 0.4744554758, green: 0.4745410681, blue: 0.4744500518, alpha: 1)
        }
        
        struct Layout {
            static let buttonHasBorder = true
            static let buttonBorderWidth = 5
        }
    }
}
