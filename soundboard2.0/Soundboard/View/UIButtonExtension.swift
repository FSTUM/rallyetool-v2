//
//  UIButtonExtension.swift
//  Soundboard
//
//  Created by Dominic Henze on 24.09.19.
//  Copyright © 2019 Dominic Henze. All rights reserved.
//

import UIKit

extension UIButton {
    func highlighted(_ highlighted: Bool) {
        self.backgroundColor = highlighted ? Config.Detail.Color.buttonHighlightColor : Config.Detail.Color.buttonColor
    }
}
