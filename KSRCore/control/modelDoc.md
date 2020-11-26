An example of a model:  
  
model.json
```
{  
    'name': 'modelRoot',  
    'type': 'Component',  
    'position': [0,0.2,0],  
    'rotation': [0,0,0],  
    'children':[  
        {  
            'name': 'arm',  
            'type': 'Joint',  
            'position': [0,0,0.3],  
            'rotation': [80,90,0],  
            'axis': [0, 0, 90],  
            'limits': {  
                'min': 10,  
                'max': 90,  
                'speed': 8  
            }  
            'children':[  
                {  
                    'name': 'hand',  
                    'type': 'Joint',  
                    'position': [0,0,0],  
                    'rotation': [0,0,0],  
                    'axis': [0, 0, 90],  
                    'limits': {  
                        'min': -30,  
                        'max': 60,  
                        'speed': 12  
                    }  
                }  
            ]  
        },  
        {  
            'name': 'wheel1',  
            'type': 'Joint',  
            'position': [-0.2,0,0],  
            'rotation': [0,0,270],  
            'axis': [0, 0, 270],  
            'limits': {  
                'speed': 60  
            }  
        }  
        {  
            'name': 'wheel2',  
            'type': 'Joint',  
            'position': [0.2,0,0],  
            'rotation': [0,0,90],  
            'axis': [0, 0, 90],  
            'limits': {  
                'speed': 60  
            }  
        }  
    ]  
}  
```

